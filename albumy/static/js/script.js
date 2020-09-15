$(function () {
    var flash = null;

    function toast(body) {
        clearTimeout(flash);
        var $toast = $('#toast');
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
});
