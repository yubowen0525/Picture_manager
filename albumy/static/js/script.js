$(function () {
    var flash = null;

    //ajax扩展增加CSRF保护
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrf_token);
            }
        }
    });

    $(document).ajaxError(function (event, request, settings) {
        var message = null;
        if (request.responseJSON && request.responseJSON.hasOwnProperty('message')) {
            message = request.responseJSON.message;
        } else if (request.responseText) {
            var IS_JSON = true;
            try {
                var data = JSON.parse(request.responseText);
            } catch (err) {
                IS_JSON = false;
            }
            if (IS_JSON && data !== undefined && data.hasOwnProperty('message')) {
                message = JSON.parse(request.responseText).message;
            } else {
                message = default_error_message;
            }
        } else {
            message = default_error_message;
        }
        toast(message, 'error');
    });


    function toast(body, category) {
        clearTimeout(flash);
        var $toast = $('#toast');
        if (category === 'error') {
            $toast.css('background-color', 'red')
        } else {
            $toast.css('background-color', '#333')
        }
        $toast.text(body).fadeIn();
        flash = setTimeout(function () {
            $toast.fadeOut();
        }, 3000);
    }

    var hover_timer = null;

    function show_profile_popover(e) {
        var $el = $(e.target);

        hover_timer = setTimeout(function () {
            hover_timer = null;
            $.ajax({
                type: 'GET',
                url: $el.data('href'),
                // data服务器返回的值
                success: function (data) {
                    $el.popover({
                        html: true,         // 使用HTML渲染
                        content: data,      // 服务端返回的数据
                        trigger: 'manual',  // 设置手动启动
                        animation: false    //关闭默认动画
                    });
                    $el.popover('show');    // 显示弹窗
                    $('.popover').on('mouseleave', function () {
                        setTimeout(function () {
                            $el.popover('hide');
                        }, 200);
                    });
                },
                error: function (error) {
                    toast('Server error, please try again later.');
                }
            });
        }, 500);
    }

    function hide_profile_popover(e) {
        var $el = $(e.target);

        if (hover_timer) {
            clearTimeout(hover_timer);
            hover_timer = null;
        } else {
            setTimeout(function () {
                if (!$('.popover:hover').length) {
                    $el.popover('hide');
                }
            }, 200);
        }
    }

    function update_followers_count(id) {
        var $el = $('#followers-count-' + id);
        $.ajax({
            type: 'GET',
            url: $el.data('href'),
            success: function (data) {
                $el.text(data.count);
            }
        });
    }

    function follow(e) {
        var $el = $(e.target);
        var id = $el.data('id');

        $.ajax({
            type: 'POST',
            url: $el.data('href'),
            success: function (data) {
                $el.prev().show();
                $el.hide();
                update_followers_count(id)
                toast(data.message)
            }
        });
    }

    function unfollow(e) {
        var $el = $(e.target);
        var id = $el.data('id');

        $.ajax({
            type: 'POST',
            url: $el.data('href'),
            success: function (data) {
                $el.next().show();
                $el.hide();
                update_followers_count(id);
                toast(data.message);
            }
        });
    }

    function update_notifications_count() {
        var $el = $('#notification-badge');
        $.ajax({
            type: 'GET',
            url: $el.data('href'),
            success: function (data) {
                if (data.count === 0) {
                    $('#notification-badge').hide();
                } else {
                    $el.show();
                    $el.text(data.count)
                }
            }
        })
    }

    if (is_authenticated) {
        setInterval(update_notifications_count, 30000);
    }

    //监听整个DOM 事件,选择器，触发的回调函数
    $(document).on('click', '.follow-btn', follow.bind(this));
    $(document).on('click', '.unfollow-btn', unfollow.bind(this));

    $('.profile-popover').hover(show_profile_popover.bind(this), hide_profile_popover.bind(this));


    // hide or show tag edit form
    $('#tag-btn').click(
        function () {
            $('#tags').hide();
            $('#tag-form').show();
        }
    );
    $('#cancel-tag').click(function () {
        $('#tag-form').hide();
        $('#tags').show();
    });
    // hide or show description edit form
    $('#description-btn').click(function () {
        $('#description').hide();
        $('#description-form').show();
    });

    $('#cancel-description').click(function () {
        $('#description-form').hide();
        $('#description').show();
    });
    // on 创建监听函数，当id值为confirm-delete触发show.bs.model事件也就是打开模态框
    // 找到属性为delete-form的表单，将它的action属性值设置为打开模态框按钮的元素的data-href属性值
    // 模态框的触发按钮通过对传入回调函数的事件对象e调用relatedTarget属性
    $('#confirm-delete').on('show.bs.modal', function (e) {
        $('.delete-form').attr('action', $(e.relatedTarget).data('href'));
    });

    $("[data-toggle='tooltip']").tooltip({title: moment($(this).data('timestamp')).format('lll')})

    function update_collectors_count(id) {
        $.ajax({
            type: 'GET',
            url: $('#collectors-count-' + id).data('href'),
            success: function (data) {
                console.log(data);
                $('#collectors-count-' + id).text(data.count);
            }
        });
    }

    function collect(e) {
        var $el = $(e.target);
        var id = $el.data('id');

        $.ajax({
            type: 'POST',
            url: $el.data('href'),
            success: function (data) {
                $el.prev().show();
                $el.hide();
                update_collectors_count(id);
                toast(data.message);
            }
        });
    }

    function uncollect(e) {
        var $el = $(e.target);
        var id = $el.data('id');
        $.ajax({
            type: 'POST',
            url: $el.data('href'),
            success: function (data) {
                $el.next().show();
                $el.hide();
                update_collectors_count(id);
                toast(data.message);
            }
        });
    }

    $(document).on('click', '.collect-btn', collect.bind(this));
    $(document).on('click', '.uncollect-btn', uncollect.bind(this));

});
